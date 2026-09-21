import {defineField, defineType} from 'sanity'

export const patch = defineType({
  name: 'patch',
  title: 'Patch',
  type: 'document',
  fields: [
    defineField({
      name: 'sha',
      title: 'Commit SHA',
      type: 'string',
      validation: (Rule) => Rule.required(),
      description: 'Short or full. B1 is dd1a654. B9 source is 872507f.',
    }),
    defineField({
      name: 'branch',
      title: 'Branch',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'inMain',
      title: 'In origin/main',
      type: 'boolean',
      initialValue: false,
      validation: (Rule) => Rule.required(),
      description: 'False until merged. Do not infer from "public on GitHub."',
    }),
    defineField({
      name: 'url',
      title: 'Commit URL',
      type: 'url',
    }),
    defineField({
      name: 'prUrl',
      title: 'Pull request URL',
      type: 'url',
    }),
    defineField({
      name: 'findings',
      title: 'Findings this patch implements',
      type: 'array',
      of: [{type: 'reference', to: [{type: 'finding'}]}],
    }),
    defineField({
      name: 'credits',
      title: 'Credits (commit body names the outsider)',
      type: 'text',
      rows: 3,
    }),
  ],
  preview: {
    select: {title: 'sha', subtitle: 'branch'},
  },
})
